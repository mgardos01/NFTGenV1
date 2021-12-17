from PIL import Image
import argparse
from tqdm import tqdm
from collections import defaultdict
import os
import itertools
import re


class Piece():
    def __init__(self, filepath):
        filename = os.path.basename(filepath)
        self.image = Image.open(filepath)
        self.name = filename
        self.pieceType = findPieceType(filename)


class Author():
    def __init__(self):
        self.name = ""


def get_valid_filename(s):
    """ Turns a string into a valid filename.
    @param s: string to be modified.
    @return: filename-save modified string.
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def findPieceType(filename):
    """ Determines all piece types from a filename.
    @param filename: filename to be searched.
    @return: a list of each type of that file.
    """
    pieceTypes = re.findall(
        r'(?<=_)[A-Z-]*(?=_)', filename)  # (?<=_)[A-Z_]*(?=_) matches all caps between two underscores
    if not pieceTypes:
        return []  # ["NONE_TYPE"]
    else:
        return pieceTypes


def displayAttributes(sources_folder_path, required_types):
    """ Displays a list of attributes and indicates which will always be included in the batch image set
    @param sources_folder_path: the folder path to the source images
    @param required_types: a list of attributes that every batch generated image will share
    @return: void. 
    """
    attributes = []
    for file in os.listdir(sources_folder_path):
        attributes.extend(findPieceType(file))
    # BACKGROUND not considered
    if (len(attributes) < 2):
        print("There are no attributes!")
        return
    print(f"There are {len(attributes) - 1} different attributes: ")
    print(f"(All images will have starred attributes)")
    print(f"{'NAME':^15}{'FREQUENCY':^15}")
    for item in sorted(set(attributes) - {"BACKGROUND"}):
        if item in required_types or not required_types:
            # BACKGROUND not considered
            print(
                f"{'★ ' + item:^15}{attributes.count(item)/(len(attributes) - 1):^15.2%}")
        else:
            # BACKGROUND not considered
            print(f"{item:^15}{attributes.count(item)/(len(attributes) - 1):^15.2%}")


def getTypeRequirement(piecetypes):
    """ Returns a list of the pieceTypes that the user wants every image to contain.
    @param: list of pieceTypes from command line arg.
    @return: aa list of the pieceTypes that the user wants every image to contain.
    """
    return set(word.upper() for word in piecetypes)


def openingMessage():
    """ Prints the opening message.
    @param: void.
    @return: filename-save modified string.
    """
    print("""
    ███╗   ██╗███████╗████████╗ ██████╗ ███████╗███╗   ██╗    ██╗   ██╗ ██╗
    ████╗  ██║██╔════╝╚══██╔══╝██╔════╝ ██╔════╝████╗  ██║    ██║   ██║███║
    ██╔██╗ ██║█████╗     ██║   ██║  ███╗█████╗  ██╔██╗ ██║    ██║   ██║╚██║
    ██║╚██╗██║██╔══╝     ██║   ██║   ██║██╔══╝  ██║╚██╗██║    ╚██╗ ██╔╝ ██║
    ██║ ╚████║██║        ██║   ╚██████╔╝███████╗██║ ╚████║     ╚████╔╝  ██║
    ╚═╝  ╚═══╝╚═╝        ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═══╝      ╚═══╝   ╚═╝                                 
    """)


def getSourceFolder(foldername):
    """ Asks for and returns the source folder name and folder path.
    @param: foldername from command line arg.
    @return: the source folder name and folder path.
    """
    sources_folder_name = get_valid_filename(foldername)
    sources_folder_path = os.path.join(os.getcwd(), sources_folder_name)
    if not os.path.isdir(sources_folder_path):
        raise Exception(
            f"ERROR: There is not a folder called /{sources_folder_name} in current directory.")
    if not any('BACKGROUND' in filename for filename in os.listdir(sources_folder_path)):
        raise Exception(
            f"ERROR: There is no explicitly typed BACKGROUND image.")
    return sources_folder_name, sources_folder_path


def getDestinationFolder(foldername):
    """ Asks for and returns the destination folder name and folder path.
    @param: foldername from command line arg.
    @return: the destination folder name and folder path.
    """
    destination_folder_name = get_valid_filename(foldername)
    destination_folder_path = os.path.join(
        os.getcwd(), destination_folder_name)

    if not os.path.isdir(destination_folder_path):
        print(f"Creating folder /{destination_folder_name}...")
        os.mkdir(destination_folder_path)

    return destination_folder_name, destination_folder_path


def getImagePrefix(prefix):
    """ Asks for and returns the image prefix .
    @param: prefix from command line arg.
    @return: the image prefix.
    """
    image_prefix = get_valid_filename(prefix)
    return image_prefix


def populateSourcesAndBackground(sources_folder_path):
    """ From the source folder path, creates a Piece from the background and a list of Pieces from the sources. 
    @param sources_folder_path: the folder path to the folder holding the source image files.
    @return: the background Piece and a list of source Pieces.
    """
    sources = []  # list of source images
    for file_name in os.listdir(sources_folder_path):
        file_path = os.path.join(sources_folder_path, file_name)
        if file_name.endswith(".png"):
            if "BACKGROUND" in findPieceType(file_name):
                background = Piece(file_path)
            else:
                sources.append(Piece(file_path))
    return background, sources


def sourcesToValidCombinations(sources):
    """ From a list of source Pieces, creates a list of tuples of every combination of those Pieces, then returns a filtered list of them. 
    @param sources: A list of tuples of source Pieces.
    @return: A filtered list of tuples of source Pieces.
    """
    unfiltered_combinations = []
    for i in range(1, len(sources)):
        unfiltered_combinations.extend(
            list(itertools.combinations(sources, i)))
    unfiltered_combinations.append(sources)
    return filterValidCombinations(unfiltered_combinations)


def filterValidCombinations(unfiltered_combinations):
    """ From a list of tuples of Pieces, returns a list of those tuples whose members have no piece types in common. 
    @param unfiltered_combinations: An list of tuples of Pieces.
    @return: A modified list of tuples of Pieces.
    """
    image_combinations = []
    for combination in unfiltered_combinations:
        pieceTypeDict = defaultdict()
        dupfound = False
        for piece in combination:
            piece_type_expanded = [
                item for sublist in pieceTypeDict.values() for item in sublist]
            if not any(piece_type for piece_type in piece.pieceType if piece_type in piece_type_expanded):
                pieceTypeDict[piece] = piece.pieceType
            else:
                dupfound = True
        if not dupfound:
            image_combinations.append(tuple(pieceTypeDict.keys()))
    return image_combinations


def filterRequiredTypes(sources, required_types):
    """ From a list of tuples of Pieces, returns a list of those tuples whose members have no piece types in common. 
    @param sources: An list of tuples of Pieces.
    @param required_types: a list of the types to use as the filter
    @return: A modified list of tuples of Pieces.
    """
    image_combinations = []
    for tup in sources:
        c = set()
        for image in tup:
            for item in image.pieceType:
                c.add(item)
        if required_types.issubset(c):
            image_combinations.append(tup)
    return image_combinations


def batchImageProcess(image_combinations, background, destination_folder_path, image_prefix):
    """ Saves an image from each combination of Pieces into a destination folder. 
    @param image_combinations: A list of tuples of each combination of Pieces to be saved to an image.
    @param background: the background for every image to be saved. 
    @param destination_folder_path: the destination folder path for the images to be saved to.
    @param image_prefix: the prefix for each image to be saved with.
    @return: void.
    """
    print("Generating images...")
    for index, comb in enumerate(tqdm(image_combinations)):
        background_copy = background.image.copy()
        for item in comb:
            item.image.convert("RGBA")
            background_copy.paste(item.image, mask=item.image)
        background_copy.save(os.path.join(
            destination_folder_path, f"{image_prefix}_{index}.png"))


def main():
    openingMessage()
    sources_folder_name, sources_folder_path = getSourceFolder(
        args.input_folder_name)
    destionation_folder_name, destination_folder_path = getDestinationFolder(
        args.output_folder_name)
    image_prefix = getImagePrefix(args.image_prefix)
    if args.attributes:
        required_types = getTypeRequirement(args.attributes)
    else:
        required_types = set()
    displayAttributes(sources_folder_name, required_types)

    background, sources = populateSourcesAndBackground(sources_folder_path)

    image_combinations = filterRequiredTypes(
        sourcesToValidCombinations(sources), required_types)

    batchImageProcess(image_combinations, background,
                      destination_folder_path, image_prefix)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch image processor.")
    parser.add_argument("-i", "--input-folder-name",
                        help="Name of input (source) folder in current directory", required=True)
    parser.add_argument("-o", "--output-folder-name",
                        help="Name of output folder in current directory", required=True)
    parser.add_argument("-p", "--image-prefix",
                        help="Name of the prefix for each batch generated image (default: img)", default="img")
    parser.add_argument(
        "-a", "--attributes", help="List the attributes that you want every batch-generated image to share", nargs="+")
    args = parser.parse_args()
    main()
